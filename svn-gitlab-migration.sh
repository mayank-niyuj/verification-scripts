# This script takes three arguments -
# 1. GitLab user name
# 2. GitLab user password
# 3. Repository name which you want to migrate

#!/bin/bash

t_start_time=$(date +%s)

# mkdir /home/mayank/migration-test/subdir/$3
# cd /home/mayank/migration-test/subdir/$3
mkdir /home/mayank/migration-test/subdir/auto
cd /home/mayank/migration-test/subdir/auto

c_start_time=$(date +%s)

# svn2git http://localhost:81/svn/$3 --trunk trunk --branches branches --tags tags --authors /home/mayank/migration-test/subdir/authors.txt
svn2git http://localhost:81/svn/ilsubversion/sp/ --trunk trunk --branches branches --tags tags --authors /home/mayank/migration-test/subdir/authors.txt

c_end_time=$(date +%s)

echo "########### Converted SVN Code in Git Format ###########"

git remote add origin http://$1:$2@10.11.14.195/root/sp.git

echo "########### GitLab Origin Added ###########"

git branch -a | grep -v svn/tags > all-branches.txt

cat all-branches.txt | awk -F / '{ print $(NF) }' > branches.txt

sed -i '/@/d' branches.txt

echo "########### Converted SVN Code in Git Format ###########"

git remote add origin http://$1:$2@10.11.14.195/root/sp.git

echo "########### GitLab Origin Added ###########"

git branch -a | grep -v svn/tags > all-branches.txt

cat all-branches.txt | awk -F / '{ print $(NF) }' > branches.txt

sed -i '/@/d' branches.txt
echo "Do you want to migrate all branches?(yes/no)"
read VAR
if [[ $VAR == yes ]]
then
  for branch in `cat branches.txt`
    do
      git checkout -b $branch svn/$branch
      git push origin $branch
   done
elif [[ $VAR == no ]]
then
  echo "Select the branches you want to migrate one by one from the list"
  echo "$(cat branches.txt)"
  read BRANCH
  echo $BRANCH > branch-list.txt
  git checkout -b $BRANCH svn/$BRANCH
  git push origin $BRANCH
  echo "Do you want to add more branches?(yes/no)"
  read output
  while [[ $output == yes ]]
  do
    cat branches.txt
    echo "Enter the branch name"
    read BRANCH
    git checkout -b $BRANCH svn/$BRANCH
    git push origin $BRANCH
    echo "Do you want to add more branches?(yes/no)"
    read output
  done
fi

echo "########### Branches are migrated on GitLab from SVN ###########"

git branch -a | grep svn/tags > all-tags.txt

cat all-tags.txt | awk -F / '{ print $(NF) }' > tags.txt

sed -i '/@/d' tags.txt

echo "Do you want to migrate all tags?(yes/no)"
read VAR
if [[ $VAR == yes ]]
then
  for tag in `cat tags.txt`
    do
      git tag $tag svn/tags/$tag
      git push origin $tag
   done
elif [[ $VAR == no ]]
then
  echo "Select the tags you want to migrate one by one from the list"
  echo "$(cat tags.txt)"
  read TAG
  echo $TAG > tag-list.txt
  git tag $TAG svn/tags/$TAG
  git push origin $TAG
  echo "Do you want to add more tags?(yes/no)"
  read output
  while [[ $output == yes ]]
  do
    cat tags.txt
    echo "Enter the tag name"
    read TAG
    git tag $TAG svn/tags/$TAG
    git push origin $TAG
    echo "Do you want to add more tags ?(yes/no)"
    read output
  done
fi

echo "########### Tags are migrated on GitLab from SVN ###########"

t_end_time=$(date +%s)

runtime=$(python3 -c "print(${c_end_time} - ${c_start_time})")
echo "SVN to GIT conversion time was $runtime seconds"

total_runtime=$(python3 -c "print(${t_end_time} - ${t_start_time})")
echo "SVN to GIT migration time was $total_runtime seconds"
